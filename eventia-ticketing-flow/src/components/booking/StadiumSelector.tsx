import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { 
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { ChevronRight, Info, MapPin, Star, Smartphone } from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import { api } from '@/lib/api';
import { Skeleton } from '@/components/ui/skeleton';

interface StadiumSection {
  section_id: string;
  name: string;
  capacity: number;
  price: number;
  description: string | null;
  availability: number;
  color_code: string;
  is_vip: boolean;
}

interface Stadium {
  stadium_id: string;
  name: string;
  city: string;
  country: string;
  capacity: number;
  sections: StadiumSection[];
  facilities: Array<{
    name: string;
    icon: string | null;
    description: string | null;
  }> | null;
  description: string | null;
  image_url: string | null;
  ar_model_url: string | null;
  is_active: boolean;
}

interface StadiumSelectorProps {
  eventId: string;
  onSelect: (stadium: Stadium) => void;
}

const StadiumSelector: React.FC<StadiumSelectorProps> = ({ eventId, onSelect }) => {
  const [stadiums, setStadiums] = useState<Stadium[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStadium, setSelectedStadium] = useState<Stadium | null>(null);
  const [selectedSections, setSelectedSections] = useState<{ [key: string]: number }>({});
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStadiums = async () => {
      try {
        setLoading(true);
        const response = await api.get('/stadiums?active_only=true');
        
        // Validate stadium data structure and attach default values if needed
        const processedStadiums = response.data.stadiums.map((stadium: Partial<Stadium>) => {
          // Ensure each stadium has properly formatted sections
          const processedSections = (stadium.sections || []).map((section: Partial<StadiumSection>) => {
            return {
              section_id: section.section_id || `section-${Math.random().toString(36).substr(2, 9)}`,
              name: section.name || 'Unknown Section',
              capacity: section.capacity || 100,
              price: section.price || 1000,
              description: section.description || null,
              availability: section.availability || 100,
              color_code: section.color_code || '#2563EB',
              is_vip: section.is_vip || false
            };
          });
          
          return {
            ...stadium,
            sections: processedSections,
            // Set default values for required fields if they're missing
            stadium_id: stadium.stadium_id || `stadium-${Math.random().toString(36).substr(2, 9)}`,
            name: stadium.name || 'Unknown Stadium',
            city: stadium.city || 'Unknown City',
            country: stadium.country || 'India',
            capacity: stadium.capacity || 10000,
            image_url: stadium.image_url || '/placeholder-stadium.jpg'
          } as Stadium;
        });
        
        setStadiums(processedStadiums);
        
        // Pre-select the first stadium if available
        if (processedStadiums.length > 0) {
          setSelectedStadium(processedStadiums[0]);
        }
      } catch (err) {
        console.error('Failed to fetch stadiums', err);
        // If the API fails, use mock data for development/testing
        const mockStadiums = generateMockStadiums();
        setStadiums(mockStadiums);
        
        if (mockStadiums.length > 0) {
          setSelectedStadium(mockStadiums[0]);
        } else {
          setError('Failed to load stadiums. Please try again later.');
          toast({
            title: 'Error',
            description: 'Failed to load stadiums. Please try again later.',
            variant: 'destructive',
          });
        }
      } finally {
        setLoading(false);
      }
    };

    fetchStadiums();
  }, []);

  // Generate mock stadiums as fallback if API fails
  const generateMockStadiums = (): Stadium[] => {
    return [
      {
        stadium_id: 'mock-narendra-modi-stadium',
        name: 'Narendra Modi Stadium',
        city: 'Ahmedabad',
        country: 'India',
        capacity: 132000,
        description: 'The largest cricket stadium in the world',
        image_url: 'https://placehold.co/600x400/007ACC/FFF?text=Modi+Stadium',
        ar_model_url: null,
        is_active: true,
        facilities: null,
        sections: [
          {
            section_id: 'premium-east',
            name: 'Premium East',
            capacity: 5000,
            price: 5000,
            description: 'Premium seats on the east side',
            availability: 4500,
            color_code: '#FF2D55',
            is_vip: true
          },
          {
            section_id: 'north-stand',
            name: 'North Stand',
            capacity: 10000,
            price: 2000,
            description: 'Standard seats on the north side',
            availability: 8000,
            color_code: '#5AC8FA',
            is_vip: false
          },
          {
            section_id: 'south-stand',
            name: 'South Stand',
            capacity: 10000,
            price: 2000,
            description: 'Standard seats on the south side',
            availability: 9500,
            color_code: '#34C759',
            is_vip: false
          }
        ]
      },
      {
        stadium_id: 'mock-eden-gardens',
        name: 'Eden Gardens',
        city: 'Kolkata',
        country: 'India',
        capacity: 68000,
        description: 'One of the most iconic cricket stadiums',
        image_url: 'https://placehold.co/600x400/FF2D55/FFF?text=Eden+Gardens',
        ar_model_url: null,
        is_active: true,
        facilities: null,
        sections: [
          {
            section_id: 'clubhouse',
            name: 'Clubhouse',
            capacity: 3000,
            price: 6000,
            description: 'Premium clubhouse seating',
            availability: 2500,
            color_code: '#FF9500',
            is_vip: true
          },
          {
            section_id: 'east-stand',
            name: 'East Stand',
            capacity: 15000,
            price: 1500,
            description: 'Standard seats on the east side',
            availability: 12000,
            color_code: '#5856D6',
            is_vip: false
          }
        ]
      }
    ];
  };

  const handleStadiumSelect = (stadium: Stadium) => {
    setSelectedStadium(stadium);
    setSelectedSections({});
  };

  const handleSectionSelect = (sectionId: string, quantity: number) => {
    if (quantity === 0) {
      const newSelections = { ...selectedSections };
      delete newSelections[sectionId];
      setSelectedSections(newSelections);
    } else {
      setSelectedSections({
        ...selectedSections,
        [sectionId]: quantity,
      });
    }
  };

  const handleContinue = () => {
    // Filter selected sections and include their details
    if (!selectedStadium) return;

    // Call the onSelect callback with the selected stadium
    onSelect(selectedStadium);
  };

  const handleViewAR = (stadiumId: string) => {
    navigate(`/ar-preview/${stadiumId}`);
  };

  // Calculate total tickets and amount
  const totalTickets = Object.values(selectedSections).reduce((sum, qty) => sum + qty, 0);
  const totalAmount = selectedStadium 
    ? selectedStadium.sections.reduce((sum, section) => {
        const qty = selectedSections[section.section_id] || 0;
        return sum + (section.price * qty);
      }, 0)
    : 0;

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-12 w-full" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <p className="text-red-500">{error}</p>
          <Button variant="outline" onClick={() => window.location.reload()} className="mt-4">
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold tracking-tight">Select a Stadium</h2>
      
      {/* Stadium Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {stadiums.map((stadium) => (
          <Card 
            key={stadium.stadium_id} 
            className={`cursor-pointer transition-all ${
              selectedStadium?.stadium_id === stadium.stadium_id 
                ? 'border-2 border-primary' 
                : 'hover:border-gray-300'
            }`}
            onClick={() => handleStadiumSelect(stadium)}
          >
            <CardHeader className="pb-2">
              <CardTitle className="flex justify-between items-center">
                <span>{stadium.name}</span>
                {stadium.ar_model_url && (
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button 
                          variant="ghost" 
                          size="icon"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleViewAR(stadium.stadium_id);
                          }}
                        >
                          <Smartphone className="h-5 w-5" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>View in AR</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                )}
              </CardTitle>
              <CardDescription className="flex items-center">
                <MapPin className="h-4 w-4 mr-1" />
                {stadium.city}, {stadium.country}
              </CardDescription>
            </CardHeader>
            <div className="relative h-40 overflow-hidden">
              <img 
                src={stadium.image_url || '/placeholder-stadium.jpg'} 
                alt={stadium.name} 
                className="w-full h-full object-cover"
              />
            </div>
            <CardFooter className="pt-4 pb-2 flex justify-between items-center">
              <div className="flex items-center text-sm text-gray-500">
                <span>Capacity: {stadium.capacity.toLocaleString()}</span>
              </div>
              <Badge variant={selectedStadium?.stadium_id === stadium.stadium_id ? "default" : "outline"}>
                {selectedStadium?.stadium_id === stadium.stadium_id ? "Selected" : "Select"}
              </Badge>
            </CardFooter>
          </Card>
        ))}
      </div>

      {/* Section Selection */}
      {selectedStadium && (
        <Card>
          <CardHeader>
            <CardTitle>Select Seats at {selectedStadium.name}</CardTitle>
            <CardDescription>
              Select sections and the number of seats you want to book
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {selectedStadium.sections.map((section) => (
                <div 
                  key={section.section_id}
                  className="p-4 border rounded-lg flex flex-col md:flex-row justify-between items-start md:items-center gap-4"
                  style={{ borderColor: section.color_code }}
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium">{section.name}</h3>
                      {section.is_vip && (
                        <Badge variant="secondary">VIP</Badge>
                      )}
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-6 w-6">
                              <Info className="h-4 w-4" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>{section.description || `Seats in the ${section.name}`}</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </div>
                    <p className="text-lg font-bold">₹{section.price.toLocaleString()}</p>
                    <p className="text-sm text-gray-500">Available: {section.availability}</p>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Button 
                      variant="outline" 
                      size="icon"
                      onClick={() => {
                        const current = selectedSections[section.section_id] || 0;
                        if (current > 0) {
                          handleSectionSelect(section.section_id, current - 1);
                        }
                      }}
                      disabled={!selectedSections[section.section_id]}
                    >
                      -
                    </Button>
                    <span className="w-8 text-center">
                      {selectedSections[section.section_id] || 0}
                    </span>
                    <Button 
                      variant="outline" 
                      size="icon"
                      onClick={() => {
                        const current = selectedSections[section.section_id] || 0;
                        if (current < section.availability) {
                          handleSectionSelect(section.section_id, current + 1);
                        }
                      }}
                      disabled={
                        (selectedSections[section.section_id] || 0) >= section.availability
                      }
                    >
                      +
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
          
          {totalTickets > 0 && (
            <>
              <Separator />
              <CardFooter className="pt-6 flex flex-col md:flex-row justify-between items-center gap-4">
                <div>
                  <p className="text-sm text-gray-500">Total selected seats: {totalTickets}</p>
                  <p className="text-xl font-bold">Total: ₹{totalAmount.toLocaleString()}</p>
                </div>
                <Button onClick={handleContinue} className="w-full md:w-auto">
                  Continue to Booking <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </CardFooter>
            </>
          )}
        </Card>
      )}

      {/* No Stadiums Available */}
      {stadiums.length === 0 && !loading && (
        <Card>
          <CardContent className="py-8 text-center">
            <p>No stadiums are currently available for booking.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default StadiumSelector; 