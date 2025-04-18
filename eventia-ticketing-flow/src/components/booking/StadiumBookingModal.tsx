import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import StadiumSelector from './StadiumSelector';
import StadiumSeatMap from './StadiumSeatMap';
import { Badge } from '@/components/ui/badge';
import { toast } from '@/hooks/use-toast';
import { api } from '@/lib/api';

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
  const [viewMode, setViewMode] = useState<'list' | 'map'>('list');
  
  // When a stadium is selected, convert its sections to include 'selected' count
  useEffect(() => {
    if (selectedStadium) {
      const sectionsWithSelection = selectedStadium.sections.map(section => ({
        ...section,
        selected: 0,
        color_code: section.color_code || '#2563EB',
        is_vip: section.is_vip || false
      }));
      setSelectedSections(sectionsWithSelection);
    }
  }, [selectedStadium]);

  const handleStadiumSelect = (stadium: Stadium) => {
    setSelectedStadium(stadium);
    setSelectedTab('sections');
  };
  
  const handleSectionSelect = (sectionId: string, quantity: number) => {
    setSelectedSections(prev => 
      prev.map(section => 
        section.section_id === sectionId 
          ? { ...section, selected: quantity } 
          : section
      )
    );
  };

  const handleContinue = () => {
    setSelectedTab('review');
  };
  
  const calculateTotal = () => {
    return selectedSections.reduce((total, section) => {
      const quantity = section.selected || 0;
      return total + (section.price * quantity);
    }, 0);
  };

  const totalTickets = selectedSections.reduce((sum, section) => sum + (section.selected || 0), 0);
  const totalAmount = calculateTotal();
  
  const handleProceedToCheckout = () => {
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
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-4xl max-h-[90vh] overflow-y-auto" aria-describedby="stadium-booking-description">
        <DialogHeader>
          <DialogTitle className="text-xl">Book Tickets for {eventTitle}</DialogTitle>
          <p id="stadium-booking-description" className="sr-only">Select a stadium, choose your seats, and proceed to checkout</p>
        </DialogHeader>
        
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
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium">Select seats at {selectedStadium.name}</h3>
                  <div className="flex space-x-2">
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
                  </div>
                </div>

                {viewMode === 'map' ? (
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
                ) : (
                  <div className="space-y-4">
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
              
              <div className="flex justify-between items-center">
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
        
        <DialogFooter className="flex justify-end">
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