import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { cn } from '@/lib/utils';
import { Info, Users, Star, Eye, ZoomIn, ZoomOut, RotateCw, ThumbsUp, AlertCircle, Loader2 } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface Seat {
  id: string;
  row: string;
  number: number;
  price: number;
  status: 'available' | 'selected' | 'unavailable' | 'reserved';
  rating?: 'best_value' | 'hot' | 'popular' | 'limited' | null;
  view_quality?: 'excellent' | 'good' | 'limited' | null;
}

interface StadiumSection {
  section_id: string;
  name: string;
  rows: number;
  seats_per_row: number;
  price: number;
  base_price: number;
  availability: number;
  color_code: string;
  is_vip: boolean;
  seats: Seat[];
}

interface SeatViewImage {
  section_id: string;
  image_url: string;
  description: string;
}

interface PremiumStadiumViewProps {
  stadiumName: string;
  sections: StadiumSection[];
  onSeatSelect: (sectionId: string, seatId: string, selected: boolean) => void;
  totalAmount: number;
  totalSeats: number;
  timeRemaining?: number;
  seatViews?: SeatViewImage[];
}

const PremiumStadiumView: React.FC<PremiumStadiumViewProps> = ({
  stadiumName,
  sections,
  onSeatSelect,
  totalAmount,
  totalSeats,
  timeRemaining,
  seatViews = []
}) => {
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [perspective, setPerspective] = useState(40);
  const [showBestDeals, setShowBestDeals] = useState(false);
  const [viewingMode, setViewingMode] = useState<'2d' | '3d'>('2d');
  const [viewPreview, setViewPreview] = useState<SeatViewImage | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isMobile, setIsMobile] = useState(false);
  
  // Detect mobile screens and adjust layout
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);
  
  // Check if data is properly loaded
  useEffect(() => {
    if (sections && sections.length > 0) {
      // Check if sections have seat data
      const hasValidData = sections.every(section => 
        section.seats && Array.isArray(section.seats) && section.seats.length > 0
      );
      
      setIsLoading(!hasValidData);
    } else {
      setIsLoading(true);
    }
    
    // Simulate loading time if needed
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);
    
    return () => clearTimeout(timer);
  }, [sections]);

  // Memoize valid sections for performance
  const validSections = useMemo(() => 
    sections.filter(section => 
      section && section.seats && Array.isArray(section.seats) && section.seats.length > 0
    ), 
    [sections]
  );
  
  // Format time remaining
  const formatTime = (seconds?: number) => {
    if (!seconds) return null;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' + secs : secs}`;
  };

  // Handle section click
  const handleSectionClick = (sectionId: string) => {
    setActiveSection(activeSection === sectionId ? null : sectionId);
  };

  // Get a color based on seat status
  const getSeatColor = (seat: Seat) => {
    if (!seat) return 'bg-gray-400 cursor-not-allowed opacity-50';
    
    if (seat.status === 'selected') return 'bg-blue-500 hover:bg-blue-600';
    if (seat.status === 'unavailable') return 'bg-gray-400 cursor-not-allowed opacity-50';
    if (seat.status === 'reserved') return 'bg-yellow-400 cursor-not-allowed';
    
    // Available seats with ratings
    if (seat.rating === 'hot') return 'bg-red-500 hover:bg-red-600';
    if (seat.rating === 'best_value') return 'bg-green-500 hover:bg-green-600';
    if (seat.rating === 'popular') return 'bg-purple-500 hover:bg-purple-600';
    if (seat.rating === 'limited') return 'bg-orange-500 hover:bg-orange-600';
    
    // Default available seat
    return 'bg-gray-600 hover:bg-gray-700';
  };

  // Get tooltip content for seat
  const getSeatTooltip = (seat: Seat, sectionName: string) => {
    if (!seat) return 'Seat information not available';
    
    const details = [
      `${sectionName}, Row ${seat.row}, Seat ${seat.number}`,
      `Price: ₹${seat.price.toLocaleString()}`
    ];

    if (seat.rating === 'hot') details.push('⚡ Hot Ticket - Selling Fast!');
    if (seat.rating === 'best_value') details.push('💰 Best Value');
    if (seat.rating === 'popular') details.push('👥 Popular Choice');
    if (seat.rating === 'limited') details.push('⚠️ Limited Availability');
    if (seat.view_quality) details.push(`👁️ ${seat.view_quality.charAt(0).toUpperCase() + seat.view_quality.slice(1)} View`);

    return details.join('\n');
  };

  // Handle seat click
  const handleSeatClick = (section: StadiumSection, seat: Seat) => {
    if (!seat || seat.status === 'unavailable' || seat.status === 'reserved') {
      return; // Can't select unavailable or reserved seats
    }
    
    const newStatus = seat.status === 'selected' ? 'available' : 'selected';
    onSeatSelect(section.section_id, seat.id, newStatus === 'selected');
  };

  // Find view preview for section
  const findSeatView = (sectionId: string) => {
    return seatViews.find(view => view.section_id === sectionId) || null;
  };

  // Keyboard navigation handler
  const handleKeyDown = (e: React.KeyboardEvent, section: StadiumSection, seat: Seat) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleSeatClick(section, seat);
    }
  };

  // Render loading state
  if (isLoading) {
    return (
      <div className="h-[500px] w-full flex items-center justify-center bg-gray-50 rounded-lg">
        <div className="flex flex-col items-center gap-2">
          <Loader2 className="h-8 w-8 animate-spin text-primary" aria-hidden="true" />
          <p>Loading stadium seat map...</p>
          <span className="sr-only">Loading stadium seating layout, please wait</span>
        </div>
      </div>
    );
  }

  // Validate sections data
  if (validSections.length === 0) {
    return (
      <div className="h-[400px] w-full flex items-center justify-center bg-gray-50 rounded-lg">
        <div className="flex flex-col items-center gap-2 text-center px-4">
          <AlertCircle className="h-8 w-8 text-amber-500" aria-hidden="true" />
          <p className="font-medium">No seat data available</p>
          <p className="text-sm text-gray-500">The stadium seat information could not be loaded correctly.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Timer bar */}
      {timeRemaining && (
        <div className="bg-red-600 text-white p-3 rounded-md flex items-center justify-between" role="timer" aria-label="Time remaining for seat selection">
          <div className="flex items-center">
            <span className="font-medium">Time remaining:</span>
          </div>
          <div className="font-bold text-lg">{formatTime(timeRemaining)}</div>
        </div>
      )}
      
      {/* Controls and info bar */}
      <div className="flex flex-wrap justify-between items-center gap-2 p-3 bg-gray-100 rounded-lg">
        <div className="font-bold text-lg flex items-center">
          <span className="mr-2">{stadiumName}</span>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Info className="h-4 w-4 text-gray-500" aria-hidden="true" />
              </TooltipTrigger>
              <TooltipContent>
                <p className="max-w-xs">Select seats by clicking on the stadium sections below. 
                You can zoom, rotate and change the viewing angle.</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
        
        <div className="flex flex-wrap gap-2">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => setShowBestDeals(!showBestDeals)}
            className={showBestDeals ? "bg-green-100" : ""}
            aria-pressed={showBestDeals}
          >
            <Star className="h-4 w-4 mr-1" aria-hidden="true" />
            Best Deals
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => setViewingMode(viewingMode === '2d' ? '3d' : '2d')}
            aria-pressed={viewingMode === '3d'}
          >
            <Eye className="h-4 w-4 mr-1" aria-hidden="true" />
            {viewingMode === '2d' ? '3D View' : '2D View'}
          </Button>
          
          <div className="flex border rounded-md">
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => setZoom(Math.max(zoom - 0.1, 0.5))}
              aria-label="Zoom out"
            >
              <ZoomOut className="h-4 w-4" aria-hidden="true" />
            </Button>
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => setZoom(Math.min(zoom + 0.1, 1.5))}
              aria-label="Zoom in"
            >
              <ZoomIn className="h-4 w-4" aria-hidden="true" />
            </Button>
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => setRotation((rotation + 45) % 360)}
              aria-label="Rotate view"
            >
              <RotateCw className="h-4 w-4" aria-hidden="true" />
            </Button>
          </div>
        </div>
      </div>
      
      {/* 3D perspective slider - only show in 3D mode */}
      {viewingMode === '3d' && (
        <div className="flex items-center gap-2 p-2 bg-gray-100 rounded-lg">
          <span className="text-sm" id="perspective-label">Angle:</span>
          <Slider
            value={[perspective]}
            min={0}
            max={60}
            step={1}
            onValueChange={(values) => setPerspective(values[0])}
            className="w-32"
            aria-labelledby="perspective-label"
          />
        </div>
      )}
      
      {/* Legend */}
      <div className="flex flex-wrap gap-3 p-3 bg-gray-100 rounded-lg text-xs" aria-label="Seat status legend">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-gray-600 rounded-full mr-1" aria-hidden="true"></div>
          <span>Available</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-blue-500 rounded-full mr-1" aria-hidden="true"></div>
          <span>Selected</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-gray-400 rounded-full mr-1" aria-hidden="true"></div>
          <span>Unavailable</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-yellow-400 rounded-full mr-1" aria-hidden="true"></div>
          <span>Reserved</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-red-500 rounded-full mr-1" aria-hidden="true"></div>
          <span>Hot Ticket</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-green-500 rounded-full mr-1" aria-hidden="true"></div>
          <span>Best Value</span>
        </div>
      </div>
      
      {/* Main stadium visualization */}
      <div 
        className="relative h-[500px] border rounded-xl overflow-hidden bg-gradient-to-b from-blue-50 to-gray-100"
        aria-label={`Interactive ${stadiumName} seating map`}
        role="application"
      >
        {/* View preview overlay */}
        {viewPreview && (
          <div 
            className="absolute inset-0 z-30 bg-black/70 flex items-center justify-center p-6"
            role="dialog"
            aria-modal="true"
            aria-labelledby="view-preview-title"
          >
            <div className="bg-white rounded-lg max-w-lg p-4 relative">
              <button 
                className="absolute top-2 right-2 text-gray-500 hover:text-gray-800"
                onClick={() => setViewPreview(null)}
                aria-label="Close view preview"
              >
                ✕
              </button>
              <h3 id="view-preview-title" className="font-bold mb-2">View from {viewPreview.section_id}</h3>
              <img 
                src={viewPreview.image_url} 
                alt={`View from ${viewPreview.section_id} section`} 
                className="w-full rounded-md mb-2"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.src = 'https://placehold.co/600x400/007ACC/FFF?text=View+Not+Available';
                }}
              />
              <p className="text-sm text-gray-600">{viewPreview.description}</p>
            </div>
          </div>
        )}
      
        {/* Stadium container with zoom/rotation */}
        <div
          className="absolute inset-0 flex items-center justify-center"
          style={{
            transform: `scale(${zoom}) rotate(${rotation}deg)`,
            transformOrigin: 'center',
            transition: 'transform 0.3s ease'
          }}
        >
          {/* Stadium visualization - with 3D effect if enabled */}
          <div 
            className="relative"
            style={{
              perspective: viewingMode === '3d' ? `${800 - perspective * 10}px` : 'none',
              transformStyle: 'preserve-3d'
            }}
          >
            {/* Field/pitch in the center */}
            <div 
              className={cn(
                "w-80 h-48 bg-gradient-to-b from-green-400 to-green-600 rounded-[50%]",
                "border-4 border-white flex items-center justify-center",
                "absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10",
                isMobile ? "scale-75" : ""
              )}
              style={{
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)'
              }}
              aria-label="Stadium field"
            >
              {/* Field markings */}
              <div className="w-60 h-32 border-2 border-white rounded-[50%] flex items-center justify-center">
                <div className="w-20 h-20 border-2 border-white rounded-full"></div>
              </div>
            </div>
            
            {/* Stadium sections */}
            <div 
              className={cn(
                "w-[600px] h-[400px] relative",
                viewingMode === '3d' ? 'transform-gpu rotateX(25deg)' : '',
                isMobile ? "scale-75" : ""
              )}
              style={{
                transformOrigin: 'center center'
              }}
              aria-label="Stadium sections"
            >
              {/* Render each section */}
              {validSections.map((section, sectionIndex) => {
                // Calculate position around the stadium
                const numSections = validSections.length;
                const angle = (sectionIndex * (360 / numSections) + rotation) % 360;
                const radius = isMobile ? 180 : 200; // Distance from center, smaller on mobile
                
                // Calculate position using trigonometry
                const x = Math.cos((angle * Math.PI) / 180) * radius;
                const y = Math.sin((angle * Math.PI) / 180) * radius;
                
                // Determine if section should be highlighted
                const isActive = activeSection === section.section_id;
                const opacity = activeSection ? (isActive ? 1 : 0.3) : 1;
                
                // Find if section has seat view
                const hasSeatView = seatViews.some(view => view.section_id === section.section_id);
                
                return (
                  <motion.div
                    key={section.section_id}
                    className={cn(
                      "absolute cursor-pointer",
                      "transform -translate-x-1/2 -translate-y-1/2 transition-all duration-200",
                      isActive ? "z-20 ring-2 ring-blue-500" : "z-10"
                    )}
                    style={{
                      left: `calc(50% + ${x}px)`,
                      top: `calc(50% + ${y}px)`,
                      opacity,
                      backgroundColor: section.color_code || '#2563EB',
                      width: isActive ? (isMobile ? '160px' : '180px') : (isMobile ? '100px' : '120px'),
                      height: isActive ? (isMobile ? '100px' : '120px') : (isMobile ? '70px' : '80px'),
                      borderRadius: '8px',
                      boxShadow: isActive ? '0 8px 30px rgba(0, 0, 0, 0.2)' : '0 4px 6px rgba(0, 0, 0, 0.1)',
                      border: section.is_vip ? '2px solid gold' : '1px solid rgba(255,255,255,0.2)'
                    }}
                    initial={{ scale: 1 }}
                    whileHover={{ scale: 1.05 }}
                    onClick={() => handleSectionClick(section.section_id)}
                    tabIndex={0}
                    role="button"
                    aria-label={`${section.name} section, price ₹${section.price.toLocaleString()}, ${section.availability} seats available`}
                    aria-expanded={isActive}
                    aria-pressed={false}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleSectionClick(section.section_id);
                      }
                    }}
                  >
                    {/* Section header */}
                    <div className="absolute top-0 left-0 right-0 bg-black/30 p-1 text-white text-center rounded-t-lg flex justify-between items-center">
                      <span className="font-medium truncate text-xs ml-1">{section.name}</span>
                      {hasSeatView && (
                        <button
                          className="text-xs p-1 hover:bg-white/10 rounded-full" 
                          onClick={(e) => {
                            e.stopPropagation();
                            const view = findSeatView(section.section_id);
                            if (view) setViewPreview(view);
                          }}
                          aria-label={`View from ${section.name} section`}
                        >
                          <Eye className="h-3 w-3" aria-hidden="true" />
                        </button>
                      )}
                    </div>
                    
                    {/* Section info */}
                    <div className="absolute bottom-0 left-0 right-0 bg-black/30 text-white p-1 text-xs rounded-b-lg">
                      <div className="flex justify-between items-center">
                        <span>₹{section.price.toLocaleString()}</span>
                        <span>{section.availability} left</span>
                      </div>
                    </div>

                    {/* Render individual seats when section is active */}
                    {isActive && section.seats && section.seats.length > 0 && (
                      <div className="absolute inset-4 flex flex-col items-center justify-center overflow-y-auto">
                        <div 
                          className="grid gap-1"
                          style={{ 
                            gridTemplateColumns: `repeat(${Math.min(isMobile ? 8 : 10, section.seats_per_row || 10)}, minmax(0, 1fr))` 
                          }}
                          role="grid"
                          aria-label={`${section.name} section seats`}
                        >
                          {section.seats.map((seat, idx) => {
                            // Skip seats if we're showing best deals and this isn't one
                            if (showBestDeals && !seat.rating && seat.status === 'available') {
                              return null;
                            }
                            
                            if (!seat || !seat.id) {
                              return (
                                <div 
                                  key={`empty-${idx}`}
                                  className="w-4 h-4 rounded-sm bg-gray-200 opacity-20"
                                  aria-hidden="true"
                                />
                              );
                            }
                            
                            const isDisabled = seat.status === 'unavailable' || seat.status === 'reserved';
                            const isSelected = seat.status === 'selected';
                            
                            return (
                              <TooltipProvider key={seat.id}>
                                <Tooltip>
                                  <TooltipTrigger asChild>
                                    <button
                                      className={cn(
                                        "w-4 h-4 rounded-sm transition-colors",
                                        getSeatColor(seat)
                                      )}
                                      disabled={isDisabled}
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleSeatClick(section, seat);
                                      }}
                                      onKeyDown={(e) => handleKeyDown(e, section, seat)}
                                      aria-label={`Row ${seat.row}, Seat ${seat.number}, Price ₹${seat.price.toLocaleString()}, ${seat.status}`}
                                      aria-selected={isSelected}
                                      aria-disabled={isDisabled}
                                      role="gridcell"
                                      tabIndex={-1}
                                    >
                                      {seat.rating === 'hot' && <span className="text-[6px]" aria-hidden="true">⚡</span>}
                                      {seat.rating === 'best_value' && <span className="text-[6px]" aria-hidden="true">💰</span>}
                                    </button>
                                  </TooltipTrigger>
                                  <TooltipContent className="whitespace-pre-line">
                                    {getSeatTooltip(seat, section.name)}
                                  </TooltipContent>
                                </Tooltip>
                              </TooltipProvider>
                            );
                          })}
                        </div>
                      </div>
                    )}
                    
                    {/* Show empty state when section is active but has no seats */}
                    {isActive && (!section.seats || section.seats.length === 0) && (
                      <div className="absolute inset-4 flex items-center justify-center">
                        <div className="text-center text-white text-xs">
                          <AlertCircle className="h-4 w-4 mx-auto mb-1" aria-hidden="true" />
                          <p>No seat data</p>
                        </div>
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
      
      {/* Best deals recommended section */}
      {showBestDeals && (
        <Card className="bg-green-50 border-green-200">
          <CardContent className="pt-4">
            <div className="flex items-center mb-3">
              <ThumbsUp className="h-5 w-5 text-green-600 mr-2" aria-hidden="true" />
              <h3 className="font-medium">Recommended Seats</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {validSections.flatMap(section => 
                (section.seats || [])
                  .filter(seat => seat && seat.rating && seat.status === 'available')
                  .slice(0, 2)
                  .map(seat => (
                    <div 
                      key={seat.id} 
                      className="bg-white p-3 rounded-lg border border-green-200 flex justify-between shadow-sm hover:shadow-md transition-shadow"
                    >
                      <div>
                        <div className="font-medium">{section.name}</div>
                        <div className="text-sm text-gray-500">
                          Row {seat.row}, Seat {seat.number}
                        </div>
                        {seat.rating === 'hot' && (
                          <Badge className="bg-red-500 mt-1">Hot Ticket</Badge>
                        )}
                        {seat.rating === 'best_value' && (
                          <Badge className="bg-green-500 mt-1">Best Value</Badge>
                        )}
                      </div>
                      <div className="text-right">
                        <div className="font-bold">₹{seat.price.toLocaleString()}</div>
                        <Button 
                          size="sm" 
                          className="mt-1"
                          onClick={() => {
                            handleSectionClick(section.section_id);
                            setTimeout(() => {
                              handleSeatClick(section, seat);
                            }, 100);
                          }}
                        >
                          Select
                        </Button>
                      </div>
                    </div>
                  ))
              )}
              
              {validSections.flatMap(section => 
                (section.seats || []).filter(seat => seat && seat.rating && seat.status === 'available')
              ).length === 0 && (
                <div className="col-span-3 text-center p-4 bg-white rounded-lg border border-green-200">
                  <p className="text-gray-500">No recommended seats currently available</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Selection summary */}
      {totalSeats > 0 && (
        <Card className="bg-white border shadow-sm">
          <CardContent className="p-4">
            <div className="flex justify-between items-center flex-wrap gap-4">
              <div>
                <div className="text-sm text-gray-500">Selected: {totalSeats} seats</div>
                <div className="text-xl font-bold">Total: ₹{totalAmount.toLocaleString()}</div>
              </div>
              <Button size="lg">
                Continue
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Accessibility info */}
      <div className="flex items-start p-3 border border-blue-200 bg-blue-50 rounded-lg text-sm">
        <AlertCircle className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5" aria-hidden="true" />
        <div>
          <p className="font-medium text-blue-800">Accessibility Information</p>
          <p className="text-blue-700 mt-1">
            For accessible seating options or special assistance, please contact our customer support.
            Wheelchair accessible seats are available in sections North and East.
          </p>
        </div>
      </div>
    </div>
  );
};

export default PremiumStadiumView; 