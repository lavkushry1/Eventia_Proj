import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import StadiumSelector from './StadiumSelector';
import StadiumSeatMap from './StadiumSeatMap';
import CircularStadiumMap from './CircularStadiumMap';
import PremiumStadiumView from './PremiumStadiumView';
import StadiumErrorBoundary from './StadiumErrorBoundary';
import { Badge } from '@/components/ui/badge';
import { toast } from '@/hooks/use-toast';
import { api } from '@/lib/api';
import { AlertCircle } from 'lucide-react';

interface StadiumBookingModalProps {
  isOpen: boolean;
  onClose: () => void;
  eventId: string;
  eventTitle: string;
}

interface StadiumSection {
  section_id: string;
  name: string;
  price: number;
  availability: number;
  color_code: string;
  is_vip: boolean;
  quantity?: number;
  selected?: number;
}

interface Stadium {
  stadium_id: string;
  name: string;
  sections: StadiumSection[];
  // Other stadium properties not needed here
}

// Add a new interface for individual seat data
interface StadiumSeat {
  id: string;
  row: string;
  number: number;
  price: number;
  status: 'available' | 'selected' | 'unavailable' | 'reserved';
  rating?: 'best_value' | 'hot' | 'popular' | 'limited' | null;
  view_quality?: 'excellent' | 'good' | 'limited' | null;
}

// Add seat view data interface
interface SeatViewImage {
  section_id: string;
  image_url: string;
  description: string;
}

const StadiumBookingModal: React.FC<StadiumBookingModalProps> = ({
  isOpen,
  onClose,
  eventId,
  eventTitle,
}) => {
  const navigate = useNavigate();
  const [selectedTab, setSelectedTab] = useState('stadium');
  const [selectedStadium, setSelectedStadium] = useState<Stadium | null>(null);
  const [selectedSections, setSelectedSections] = useState<StadiumSection[]>([]);
  const [viewMode, setViewMode] = useState<'list' | 'map' | 'circular' | 'premium'>('list');
  const [timeRemaining, setTimeRemaining] = useState<number>(300); // 5 minutes in seconds
  const [selectedSeats, setSelectedSeats] = useState<{[key: string]: StadiumSeat[]}>({});
  const [seatViews, setSeatViews] = useState<SeatViewImage[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isMobile, setIsMobile] = useState(false);
  
  // Detect mobile screens
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);
  
  // Generate mock data for seat views when a stadium is selected
  useEffect(() => {
    try {
      if (selectedStadium) {
        // Generate mock seat view data
        const mockViews = selectedStadium.sections.slice(0, 3).map(section => ({
          section_id: section.section_id,
          image_url: `https://placehold.co/600x400/007ACC/FFF?text=View+from+${section.name}`,
          description: `This is the view from the ${section.name} section. This section offers a ${
            section.is_vip ? 'premium' : 'standard'
          } viewing experience.`
        }));
        setSeatViews(mockViews);
        setErrorMessage(null);
      }
    } catch (error) {
      console.error("Error generating seat views:", error);
      setErrorMessage("Failed to load seat views. Please try again.");
    }
  }, [selectedStadium]);

  // When a stadium is selected, convert its sections to include 'selected' count
  useEffect(() => {
    try {
      if (selectedStadium) {
        const sectionsWithSelection = selectedStadium.sections.map(section => ({
          ...section,
          selected: 0,
          color_code: section.color_code || '#2563EB',
          is_vip: section.is_vip || false
        }));
        setSelectedSections(sectionsWithSelection);
        setErrorMessage(null);
      }
    } catch (error) {
      console.error("Error processing stadium sections:", error);
      setErrorMessage("Failed to load stadium sections. Please try again.");
    }
  }, [selectedStadium]);

  // Timer countdown effect
  useEffect(() => {
    if (selectedTab === 'sections' && timeRemaining > 0) {
      const timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      
      return () => clearInterval(timer);
    }
  }, [selectedTab, timeRemaining]);

  // Reset timer when moving back to stadium selection
  useEffect(() => {
    if (selectedTab === 'stadium') {
      setTimeRemaining(300); // Reset to 5 minutes
    }
  }, [selectedTab]);

  // Time's up handler
  useEffect(() => {
    if (timeRemaining === 0) {
      toast({
        title: "Time's up!",
        description: "Your seat selection time has expired.",
        variant: "destructive"
      });
      // Optionally reset or take other actions
    }
  }, [timeRemaining]);

  const handleStadiumSelect = (stadium: Stadium) => {
    try {
      setSelectedStadium(stadium);
      setSelectedTab('sections');
      setErrorMessage(null);
    } catch (error) {
      console.error("Error selecting stadium:", error);
      setErrorMessage("Failed to select stadium. Please try again.");
    }
  };
  
  const handleSectionSelect = (sectionId: string, quantity: number) => {
    try {
      if (!sectionId) {
        console.error("Invalid section ID provided");
        return;
      }
      
      setSelectedSections(prev => 
        prev.map(section => 
          section.section_id === sectionId 
            ? { ...section, selected: quantity } 
            : section
        )
      );
      setErrorMessage(null);
    } catch (error) {
      console.error("Error selecting section:", error);
      setErrorMessage("Failed to select section. Please try again.");
    }
  };

  const handleContinue = () => {
    try {
      if (totalTickets === 0) {
        toast({
          title: "No seats selected",
          description: "Please select at least one seat to continue.",
          variant: "destructive"
        });
        return;
      }
      
      setSelectedTab('review');
      setErrorMessage(null);
    } catch (error) {
      console.error("Error continuing to review:", error);
      setErrorMessage("Failed to continue to review. Please try again.");
    }
  };
  
  const calculateTotal = () => {
    try {
      return selectedSections.reduce((total, section) => {
        const quantity = section.selected || 0;
        return total + (section.price * quantity);
      }, 0);
    } catch (error) {
      console.error("Error calculating total:", error);
      return 0;
    }
  };

  const totalTickets = selectedSections.reduce((sum, section) => sum + (section.selected || 0), 0);
  const totalAmount = calculateTotal();
  
  // Handle individual seat selection
  const handleSeatSelect = (sectionId: string, seatId: string, selected: boolean) => {
    try {
      // Find the section
      const section = selectedSections.find(s => s.section_id === sectionId);
      if (!section) {
        console.error(`Section with ID ${sectionId} not found`);
        return;
      }

      // Update section selection counts
      setSelectedSections(prev => 
        prev.map(section => 
          section.section_id === sectionId 
            ? { 
                ...section, 
                selected: (section.selected || 0) + (selected ? 1 : -1)
              } 
            : section
        )
      );

      // Track individual seats (for premium view)
      setSelectedSeats(prev => {
        const newSeats = {...prev};
        if (!newSeats[sectionId]) newSeats[sectionId] = [];
        
        // Mock a seat object if we don't have the actual one
        const mockSeat: StadiumSeat = {
          id: seatId,
          row: seatId.split('-')[0] || 'A',
          number: parseInt(seatId.split('-')[1] || '1', 10),
          price: section.price,
          status: selected ? 'selected' : 'available'
        };
        
        if (selected) {
          newSeats[sectionId] = [...newSeats[sectionId], mockSeat];
        } else {
          newSeats[sectionId] = newSeats[sectionId].filter(seat => seat.id !== seatId);
        }
        
        return newSeats;
      });
      
      setErrorMessage(null);
    } catch (error) {
      console.error("Error selecting seat:", error);
      setErrorMessage("Failed to select seat. Please try again.");
    }
  };

  // Generate sections with seat data for premium view
  const getSectionsWithSeats = () => {
    try {
      if (!selectedStadium) return [];
      
      return selectedStadium.sections.map(section => {
        // Generate mock seats for each section
        const seats: StadiumSeat[] = [];
        const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
        const seatsPerRow = isMobile ? 8 : 10;
        
        try {
          rows.forEach((row, rowIndex) => {
            for (let i = 1; i <= seatsPerRow; i++) {
              const seatId = `${row}-${i}`;
              
              // Check if this seat is already selected in our state
              const isSelected = selectedSeats[section.section_id]?.some(seat => seat.id === seatId) || false;
              
              // Deterministic randomization based on seatId to ensure consistency
              const randomSeed = seatId.charCodeAt(0) * seatId.charCodeAt(2) % 100;
              const random = randomSeed / 100;
              
              let status: 'available' | 'selected' | 'unavailable' | 'reserved' = 'available';
              let rating: 'best_value' | 'hot' | 'popular' | 'limited' | null = null;
              
              if (isSelected) {
                status = 'selected';
              } else if (random < 0.1) {
                status = 'unavailable';
              } else if (random < 0.15) {
                status = 'reserved';
              } else {
                // Only available seats can have ratings
                if (random > 0.85) rating = 'hot';
                else if (random > 0.8) rating = 'best_value';
                else if (random > 0.75) rating = 'popular';
                else if (random > 0.7) rating = 'limited';
              }
              
              seats.push({
                id: seatId,
                row,
                number: i,
                price: section.price + (rowIndex < 3 ? 500 : 0), // Premium rows cost more
                status,
                rating,
                view_quality: rowIndex < 2 ? 'excellent' : rowIndex < 5 ? 'good' : 'limited'
              });
            }
          });
        } catch (error) {
          console.error('Error generating seats for section:', section.section_id, error);
          // Return at least an empty seats array if there's an error
        }
        
        return {
          ...section,
          rows: rows.length,
          seats_per_row: seatsPerRow,
          base_price: section.price,
          seats
        };
      });
    } catch (error) {
      console.error("Error generating sections with seats:", error);
      setErrorMessage("Failed to load seat data. Please try again.");
      return [];
    }
  };

  const handleProceedToCheckout = () => {
    try {
      // Only include sections with selections
      const sectionsWithSelections = selectedSections
        .filter(section => (section.selected || 0) > 0)
        .map(section => ({
          section_id: section.section_id,
          name: section.name,
          quantity: section.selected || 0,
          price: section.price,
          subtotal: section.price * (section.selected || 0)
        }));

      if (sectionsWithSelections.length === 0) {
        toast({
          title: "No seats selected",
          description: "Please select at least one seat to continue.",
          variant: "destructive"
        });
        return;
      }
      
      // Store booking data in sessionStorage for checkout page
      const bookingData = {
        eventId,
        eventTitle,
        stadiumId: selectedStadium?.stadium_id,
        stadiumName: selectedStadium?.name,
        tickets: sectionsWithSelections,
        totalAmount
      };
      
      sessionStorage.setItem('bookingData', JSON.stringify(bookingData));
      toast({
        title: "Booking Initiated",
        description: `Proceeding to checkout for ${totalTickets} tickets.`
      });
      navigate('/checkout');
      onClose();
    } catch (error) {
      console.error("Error proceeding to checkout:", error);
      setErrorMessage("Failed to proceed to checkout. Please try again.");
    }
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl">Book Tickets for {eventTitle}</DialogTitle>
          <DialogDescription>
            Select a stadium, choose your seats, and proceed to checkout
          </DialogDescription>
        </DialogHeader>
        
        {errorMessage && (
          <div className="mb-4 p-3 bg-red-100 border border-red-300 text-red-700 rounded-md">
            <p className="flex items-center">
              <AlertCircle className="h-4 w-4 mr-2" />
              {errorMessage}
            </p>
            <Button 
              variant="ghost" 
              size="sm" 
              className="mt-1 text-xs" 
              onClick={() => setErrorMessage(null)}
            >
              Dismiss
            </Button>
          </div>
        )}
        
        <Tabs defaultValue="stadium" value={selectedTab} onValueChange={setSelectedTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="stadium">Select Stadium</TabsTrigger>
            <TabsTrigger value="sections" disabled={!selectedStadium}>Select Seats</TabsTrigger>
            <TabsTrigger value="review" disabled={totalTickets === 0}>Review & Checkout</TabsTrigger>
          </TabsList>
          
          <TabsContent value="stadium" className="py-4">
            <StadiumSelector 
              eventId={eventId} 
              onSelect={handleStadiumSelect} 
            />
          </TabsContent>
          
          <TabsContent value="sections" className="py-4">
            {selectedStadium && (
              <div className="space-y-6">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                  <h3 className="text-lg font-medium">Select seats at {selectedStadium.name}</h3>
                  <div className="flex flex-wrap gap-2">
                    <Button 
                      variant={viewMode === 'list' ? 'default' : 'outline'} 
                      size="sm" 
                      onClick={() => setViewMode('list')}
                    >
                      List View
                    </Button>
                    <Button 
                      variant={viewMode === 'map' ? 'default' : 'outline'} 
                      size="sm" 
                      onClick={() => setViewMode('map')}
                    >
                      Map View
                    </Button>
                    <Button 
                      variant={viewMode === 'circular' ? 'default' : 'outline'} 
                      size="sm" 
                      onClick={() => setViewMode('circular')}
                    >
                      Stadium View
                    </Button>
                    <Button 
                      variant={viewMode === 'premium' ? 'default' : 'outline'} 
                      size="sm" 
                      onClick={() => setViewMode('premium')}
                    >
                      Premium
                    </Button>
                  </div>
                </div>

                {viewMode === 'premium' ? (
                  <StadiumErrorBoundary stadiumName={selectedStadium.name} onSwitchView={() => setViewMode('list')}>
                    <PremiumStadiumView
                      stadiumName={selectedStadium.name}
                      sections={getSectionsWithSeats()}
                      onSeatSelect={handleSeatSelect}
                      totalAmount={totalAmount}
                      totalSeats={totalTickets}
                      timeRemaining={timeRemaining}
                      seatViews={seatViews}
                    />
                  </StadiumErrorBoundary>
                ) : viewMode === 'circular' ? (
                  <StadiumErrorBoundary stadiumName={selectedStadium.name} onSwitchView={() => setViewMode('list')}>
                    <CircularStadiumMap
                      stadiumName={selectedStadium.name}
                      sections={selectedSections}
                      onSectionSelect={handleSectionSelect}
                      totalAmount={totalAmount}
                      totalTickets={totalTickets}
                      timeRemaining={timeRemaining}
                    />
                  </StadiumErrorBoundary>
                ) : viewMode === 'map' ? (
                  <StadiumErrorBoundary stadiumName={selectedStadium.name} onSwitchView={() => setViewMode('list')}>
                    <StadiumSeatMap 
                      stadiumName={selectedStadium.name}
                      sections={selectedSections.map(section => ({
                        ...section,
                        color_code: section.color_code,
                        is_vip: section.is_vip,
                        selected: section.selected || 0
                      }))}
                      onSectionSelect={handleSectionSelect}
                    />
                  </StadiumErrorBoundary>
                ) : (
                  <div className="space-y-4">
                    {timeRemaining > 0 && selectedTab === 'sections' && (
                      <div className="bg-indigo-900 text-white py-2 px-4 rounded-md">
                        <div className="text-center">
                          <span className="font-medium">You have approximately {Math.floor(timeRemaining / 60)} minutes</span> to select your seats.
                        </div>
                      </div>
                    )}
                    
                    {selectedSections.map((section) => (
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
                          </div>
                          <p className="text-lg font-bold">₹{section.price.toLocaleString()}</p>
                          <p className="text-sm text-gray-500">Available: {section.availability}</p>
                        </div>
                        
                        <div className="flex items-center gap-2">
                          <Button 
                            variant="outline" 
                            size="icon"
                            onClick={() => {
                              const current = section.selected || 0;
                              if (current > 0) {
                                handleSectionSelect(section.section_id, current - 1);
                              }
                            }}
                            disabled={(section.selected || 0) === 0}
                            aria-label={`Decrease quantity for ${section.name}`}
                          >
                            -
                          </Button>
                          <span className="w-8 text-center">
                            {section.selected || 0}
                          </span>
                          <Button 
                            variant="outline" 
                            size="icon"
                            onClick={() => {
                              const current = section.selected || 0;
                              if (current < section.availability) {
                                handleSectionSelect(section.section_id, current + 1);
                              }
                            }}
                            disabled={(section.selected || 0) >= section.availability}
                            aria-label={`Increase quantity for ${section.name}`}
                          >
                            +
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {totalTickets > 0 && (
                  <>
                    <Separator />
                    <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                      <div>
                        <p className="text-sm text-gray-500">Total selected seats: {totalTickets}</p>
                        <p className="text-xl font-bold">Total: ₹{totalAmount.toLocaleString()}</p>
                      </div>
                      <Button onClick={handleContinue}>Continue to Review</Button>
                    </div>
                  </>
                )}
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="review" className="py-4">
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Review Your Selection</h3>
              
              {selectedStadium && (
                <div className="p-3 border rounded-md">
                  <h4 className="font-medium">{selectedStadium.name}</h4>
                </div>
              )}
              
              {selectedSections
                .filter(section => (section.selected || 0) > 0)
                .map((section) => (
                  <div key={section.section_id} className="flex justify-between items-center p-3 border rounded-md">
                    <div>
                      <div className="font-medium">{section.name}</div>
                      <div className="text-sm text-gray-500">₹{section.price.toLocaleString()} × {section.selected}</div>
                    </div>
                    <div className="font-semibold">
                      ₹{(section.price * (section.selected || 0)).toLocaleString()}
                    </div>
                  </div>
                ))}
              
              <Separator />
              
              <div className="p-4 border rounded-md bg-gray-50">
                <div className="flex justify-between font-medium">
                  <span>Total Tickets:</span>
                  <span>{totalTickets}</span>
                </div>
                <div className="flex justify-between text-lg font-bold mt-2">
                  <span>Total Amount:</span>
                  <span>₹{totalAmount.toLocaleString()}</span>
                </div>
              </div>
              
              <div className="p-4 border rounded-md bg-blue-50">
                <h4 className="font-medium text-blue-700">Important Information</h4>
                <ul className="text-sm text-blue-600 mt-2 space-y-1">
                  <li>• Tickets cannot be cancelled after purchase</li>
                  <li>• Please bring a valid ID for verification at the venue</li>
                  <li>• Gates open 2 hours before the event</li>
                </ul>
              </div>
              
              <div className="flex flex-wrap justify-between items-center gap-3">
                <Button variant="outline" onClick={() => setSelectedTab('sections')}>
                  Back to Selection
                </Button>
                <Badge variant="outline" className="px-3 py-1">
                  <span className="font-normal">Total: </span>
                  <span className="ml-1 font-bold">₹{totalAmount.toLocaleString()}</span>
                </Badge>
              </div>
            </div>
          </TabsContent>
        </Tabs>
        
        <DialogFooter className="flex justify-end flex-wrap gap-2">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          {selectedTab === 'review' && (
            <Button 
              onClick={handleProceedToCheckout}
              disabled={totalTickets === 0}
            >
              Proceed to Checkout
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default StadiumBookingModal; 